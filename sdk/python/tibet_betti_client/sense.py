"""
SENSE 2.0: Client-Side Context & Profiling
===========================================

Privacy-first client-side Sense layer voor apps.

Features:
- Local behavior profiling (blijft op device!)
- Pattern detection (wat doe je vaak?)
- Predictive suggestions (wat wil je waarschijnlijk doen?)
- Optional sync to backend (user controlled)

Author: Jasper van de Meent / Humotica
License: JOSL
"""

import time
import json
import platform
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import Counter, defaultdict
from pathlib import Path


class ClientSense:
    """Client-side Sense with privacy-first profiling"""

    def __init__(self, user_id: str, storage_dir: Optional[str] = None, privacy_mode: bool = True):
        self.user_id = user_id
        self.privacy_mode = privacy_mode

        # Local storage
        if storage_dir:
            self.storage_dir = Path(storage_dir)
        else:
            self.storage_dir = Path.home() / ".humotica" / "sense"

        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # In-memory stats
        self.local_stats = self._load_local_stats()
        self.session_start = time.time()

    # ========================================
    # ACTION RECORDING
    # ========================================

    def record_action(self, action: str, context: Optional[Dict] = None):
        """
        Record action locally (privacy-first!)

        Args:
            action: Type of action ("call", "message", "search", etc.)
            context: Optional context (sanitized for privacy)
        """
        if context is None:
            context = {}

        snapshot = {
            "timestamp": time.time(),
            "action": action,
            "target": context.get("target", "unknown"),  # Who/what
            "intent": context.get("intent", "unknown"),  # Why
            "location": self._sanitize_location(context.get("location")),
            "device": platform.system(),
            "time_of_day": self._get_time_of_day(),
            "day_of_week": datetime.now().strftime('%A').lower(),
            "result": context.get("result", "pending")
        }

        # Store locally
        if action not in self.local_stats:
            self.local_stats[action] = []

        self.local_stats[action].append(snapshot)

        # Keep only last 1000 actions per type (privacy: limited history)
        if len(self.local_stats[action]) > 1000:
            self.local_stats[action] = self.local_stats[action][-1000:]

        # Save to disk
        self._save_local_stats()

        return snapshot

    # ========================================
    # PATTERN DETECTION
    # ========================================

    def get_pattern(self, action: str) -> Dict:
        """
        Get behavior pattern for an action

        Returns:
            {
                "count": 123,
                "common_hours": [(9, 45), (14, 23), (18, 12)],
                "common_days": ["monday", "friday"],
                "common_targets": ["mama", "werk"],
                "avg_duration_min": 12.5,
                "last_used": timestamp
            }
        """
        history = self.local_stats.get(action, [])

        if not history:
            return {"count": 0, "error": "No history for this action"}

        # Analyze timing
        hours = [datetime.fromtimestamp(s["timestamp"]).hour for s in history]
        days = [s["day_of_week"] for s in history]
        targets = [s["target"] for s in history if s["target"] != "unknown"]

        hour_counts = Counter(hours)
        day_counts = Counter(days)
        target_counts = Counter(targets)

        return {
            "count": len(history),
            "common_hours": hour_counts.most_common(3),  # Top 3 hours
            "common_days": [day for day, _ in day_counts.most_common(3)],
            "common_targets": [tgt for tgt, _ in target_counts.most_common(5)],
            "last_used": max(s["timestamp"] for s in history),
            "first_used": min(s["timestamp"] for s in history)
        }

    def get_all_patterns(self) -> Dict[str, Dict]:
        """Get patterns for all actions"""
        return {
            action: self.get_pattern(action)
            for action in self.local_stats.keys()
        }

    # ========================================
    # PREDICTIONS
    # ========================================

    def predict_next_action(self) -> Optional[str]:
        """
        Predict what user will likely do next based on:
        - Current time
        - Day of week
        - Recent actions

        Returns:
            Action name or None
        """
        now = datetime.now()
        current_hour = now.hour
        current_day = now.strftime('%A').lower()

        # Score each action based on likelihood
        scores = {}

        for action, history in self.local_stats.items():
            score = 0

            # Time-based scoring
            same_hour = [h for h in history
                        if datetime.fromtimestamp(h["timestamp"]).hour == current_hour]
            score += len(same_hour) * 3  # Heavy weight for same hour

            # Day-based scoring
            same_day = [h for h in history if h["day_of_week"] == current_day]
            score += len(same_day) * 1.5

            # Recency bonus (did this recently?)
            recent = [h for h in history
                     if time.time() - h["timestamp"] < 3600]  # Last hour
            score += len(recent) * 2

            scores[action] = score

        if not scores:
            return None

        # Return highest scoring action
        best_action = max(scores, key=scores.get)

        # Only predict if confidence is reasonable
        if scores[best_action] > 5:  # Threshold
            return best_action

        return None

    def predict_target(self, action: str) -> Optional[str]:
        """
        Predict WHO/WHAT user will interact with for this action

        Example: predict_target("call") → "mama" (often called)
        """
        pattern = self.get_pattern(action)

        if pattern.get("count", 0) == 0:
            return None

        # Return most common target
        targets = pattern.get("common_targets", [])
        if targets:
            return targets[0]

        return None

    def suggest_actions(self, limit: int = 3) -> List[Dict]:
        """
        Suggest actions based on current context

        Returns:
            [
                {"action": "call", "target": "mama", "confidence": 0.85},
                {"action": "message", "target": "werk", "confidence": 0.65},
                ...
            ]
        """
        now_hour = datetime.now().hour
        suggestions = []

        for action, history in self.local_stats.items():
            # What percentage of this action happens at this hour?
            same_hour = [h for h in history
                        if datetime.fromtimestamp(h["timestamp"]).hour == now_hour]

            if len(same_hour) > 2:  # At least 3 times before
                confidence = len(same_hour) / len(history)

                target = None
                if same_hour:
                    targets = [h["target"] for h in same_hour if h["target"] != "unknown"]
                    if targets:
                        target = Counter(targets).most_common(1)[0][0]

                suggestions.append({
                    "action": action,
                    "target": target,
                    "confidence": confidence,
                    "times_done": len(same_hour)
                })

        # Sort by confidence
        suggestions.sort(key=lambda x: x["confidence"], reverse=True)

        return suggestions[:limit]

    # ========================================
    # SITUATION DETECTION
    # ========================================

    def detect_situation(self) -> Dict:
        """
        Detect current situation from local patterns

        Returns:
            {
                "time_of_day": "morning",
                "typical_activity": "call",  # What user usually does now
                "is_free": true,  # Not busy based on patterns
                "suggested_mode": "personal"  # vs "professional"
            }
        """
        now = datetime.now()
        hour = now.hour
        day = now.strftime('%A').lower()

        # Typical activity at this time?
        typical_activity = None
        max_count = 0

        for action, history in self.local_stats.items():
            same_time = [h for h in history
                        if abs(datetime.fromtimestamp(h["timestamp"]).hour - hour) <= 1]
            if len(same_time) > max_count:
                max_count = len(same_time)
                typical_activity = action

        # Is user usually free now? (low activity = free)
        recent_hour = time.time() - 3600
        all_recent = sum(
            len([h for h in history if h["timestamp"] > recent_hour])
            for history in self.local_stats.values()
        )
        is_free = all_recent < 3  # <3 actions in last hour = probably free

        # Professional vs personal mode (guess from time)
        is_weekend = now.weekday() >= 5
        is_business_hours = 9 <= hour <= 17

        mode = "personal"
        if not is_weekend and is_business_hours:
            mode = "professional"

        return {
            "time_of_day": self._get_time_of_day(),
            "day_of_week": day,
            "is_weekend": is_weekend,
            "typical_activity": typical_activity,
            "is_free": is_free,
            "suggested_mode": mode,
            "activity_level": "low" if all_recent < 3 else
                             "medium" if all_recent < 10 else "high"
        }

    # ========================================
    # PRIVACY CONTROLS
    # ========================================

    def export_data(self) -> Dict:
        """GDPR: Export all local data"""
        return {
            "user_id": self.user_id,
            "local_stats": self.local_stats,
            "patterns": self.get_all_patterns(),
            "export_date": datetime.now().isoformat(),
            "privacy_mode": self.privacy_mode
        }

    def delete_data(self):
        """GDPR: Delete all local data"""
        self.local_stats = {}
        self._save_local_stats()

        # Delete storage file
        storage_file = self.storage_dir / f"{self.user_id}_stats.json"
        if storage_file.exists():
            storage_file.unlink()

    def get_stats_summary(self) -> Dict:
        """Get summary of local statistics"""
        total_actions = sum(len(history) for history in self.local_stats.values())

        return {
            "total_actions": total_actions,
            "action_types": len(self.local_stats),
            "most_common_action": max(self.local_stats, key=lambda k: len(self.local_stats[k]))
                                 if self.local_stats else None,
            "session_duration_min": (time.time() - self.session_start) / 60,
            "storage_size_kb": self._get_storage_size() / 1024
        }

    # ========================================
    # STORAGE (Local File System)
    # ========================================

    def _load_local_stats(self) -> Dict:
        """Load stats from local storage"""
        storage_file = self.storage_dir / f"{self.user_id}_stats.json"

        if storage_file.exists():
            try:
                with open(storage_file, 'r') as f:
                    return json.load(f)
            except:
                return {}

        return {}

    def _save_local_stats(self):
        """Save stats to local storage"""
        storage_file = self.storage_dir / f"{self.user_id}_stats.json"

        with open(storage_file, 'w') as f:
            json.dump(self.local_stats, f)

    def _get_storage_size(self) -> int:
        """Get storage size in bytes"""
        storage_file = self.storage_dir / f"{self.user_id}_stats.json"

        if storage_file.exists():
            return storage_file.stat().st_size

        return 0

    # ========================================
    # HELPERS
    # ========================================

    def _get_time_of_day(self) -> str:
        """Get time of day category"""
        hour = datetime.now().hour

        if 6 <= hour < 12:
            return "morning"
        elif 12 <= hour < 18:
            return "afternoon"
        elif 18 <= hour < 22:
            return "evening"
        else:
            return "night"

    def _sanitize_location(self, location: Optional[str]) -> str:
        """Sanitize location for privacy (only keep categories)"""
        if not location:
            return "unknown"

        # Only keep general categories, not exact coordinates
        if "home" in location.lower():
            return "home"
        elif "work" in location.lower():
            return "work"
        elif "travel" in location.lower():
            return "travel"
        else:
            return "other"
