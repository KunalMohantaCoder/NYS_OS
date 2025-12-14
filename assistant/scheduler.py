"""
Scheduling and calendar management.
"""
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class Scheduler:
    """
    Manages scheduling and calendar events.
    """
    
    def __init__(self, data_dir: str = "data/assistant"):
        """
        Initialize scheduler.
        
        Args:
            data_dir: Directory to store calendar data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.calendar_file = self.data_dir / "calendar.json"
        self.events = self._load_events()
    
    def _load_events(self) -> List[Dict]:
        """Load events from file."""
        if self.calendar_file.exists():
            try:
                with open(self.calendar_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_events(self):
        """Save events to file."""
        with open(self.calendar_file, 'w', encoding='utf-8') as f:
            json.dump(self.events, f, indent=2, default=str)
    
    def add_event(self, description: str, time_str: Optional[str] = None,
                 date_str: Optional[str] = None) -> Tuple[bool, str]:
        """
        Add a new event.
        
        Args:
            description: Event description
            time_str: Time string (e.g., "3pm", "15:00")
            date_str: Date string (e.g., "tomorrow", "2024-01-15")
        
        Returns:
            Tuple of (success, message)
        """
        try:
            # Parse date and time
            event_time = self._parse_datetime(time_str, date_str)
            
            event = {
                'id': len(self.events) + 1,
                'description': description,
                'datetime': event_time.isoformat(),
                'created': datetime.now().isoformat()
            }
            
            self.events.append(event)
            self._save_events()
            
            return True, f"Scheduled event: {description} at {event_time.strftime('%Y-%m-%d %H:%M')}"
        except Exception as e:
            return False, f"Error scheduling event: {str(e)}"
    
    def _parse_datetime(self, time_str: Optional[str], date_str: Optional[str]) -> datetime:
        """Parse time and date strings into datetime object."""
        now = datetime.now()
        
        # Parse date
        if date_str:
            date_str_lower = date_str.lower()
            if date_str_lower == 'today':
                event_date = now.date()
            elif date_str_lower == 'tomorrow':
                event_date = (now + timedelta(days=1)).date()
            else:
                try:
                    event_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                except:
                    event_date = now.date()
        else:
            event_date = now.date()
        
        # Parse time
        if time_str:
            time_str_lower = time_str.lower().replace(' ', '')
            # Try parsing various formats
            try:
                if 'pm' in time_str_lower or 'am' in time_str_lower:
                    event_time = datetime.strptime(time_str_lower, '%I%p').time()
                else:
                    event_time = datetime.strptime(time_str_lower, '%H:%M').time()
            except:
                event_time = now.time()
        else:
            event_time = now.time()
        
        return datetime.combine(event_date, event_time)
    
    def list_events(self, days_ahead: int = 7) -> Tuple[bool, str, List[Dict]]:
        """
        List upcoming events.
        
        Args:
            days_ahead: Number of days ahead to show
        
        Returns:
            Tuple of (success, message, events)
        """
        try:
            now = datetime.now()
            cutoff = now + timedelta(days=days_ahead)
            
            upcoming = []
            for event in self.events:
                event_dt = datetime.fromisoformat(event['datetime'])
                if now <= event_dt <= cutoff:
                    upcoming.append(event)
            
            # Sort by datetime
            upcoming.sort(key=lambda x: x['datetime'])
            
            return True, f"Upcoming events (next {days_ahead} days):", upcoming
        except Exception as e:
            return False, f"Error listing events: {str(e)}", []
    
    def delete_event(self, event_id: int) -> Tuple[bool, str]:
        """
        Delete an event.
        
        Args:
            event_id: Event ID to delete
        
        Returns:
            Tuple of (success, message)
        """
        try:
            original_count = len(self.events)
            self.events = [e for e in self.events if e['id'] != event_id]
            
            if len(self.events) < original_count:
                self._save_events()
                return True, f"Deleted event {event_id}"
            else:
                return False, f"Event {event_id} not found"
        except Exception as e:
            return False, f"Error deleting event: {str(e)}"

