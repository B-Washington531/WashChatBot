"""Synthetic posts used to bootstrap and test the local data pipeline."""

from .tweets import Tweet

SYNTHETIC_TWEETS = (
    Tweet("syn-001", "That fourth quarter was unreal. Defense wins games!", "2025-01-01T09:00:00Z", "twitter", False, "conv-001"),
    Tweet("syn-002", "Coach said 'one more drill' and somehow we did seven 😂", "2025-01-01T10:15:00Z", "twitter", True, "conv-002"),
    Tweet("syn-003", "The rookie's footwork is already so clean.", "2025-01-02T12:30:00Z", "twitter", False, None),
    Tweet("syn-004", "Nothing like a buzzer beater to ruin a perfectly calm evening", "2025-01-03T20:45:00Z", "twitter", False, "conv-004"),
    Tweet("syn-005", "Tried the new keyboard today. The little clicky keys are dangerously satisfying", "2025-01-04T08:10:00Z", "twitter", False, None),
    Tweet("syn-006", "my laptop updated right before the meeting. classic.", "2025-01-05T14:00:00Z", "twitter", True, "conv-006"),
    Tweet("syn-007", "A tiny script just saved me 40 minutes. I love computers sometimes.", "2025-01-06T11:20:00Z", "twitter", False, None),
    Tweet("syn-008", "If the app needs 12 permissions to show me the weather, maybe it can stay mysterious", "2025-01-07T07:55:00Z", "twitter", False, "conv-008"),
    Tweet("syn-009", "coffee acquired. brain booting...", "2025-01-08T08:05:00Z", "twitter", False, None),
    Tweet("syn-010", "I went out for one thing and came home with snacks for the entire week", "2025-01-09T17:40:00Z", "twitter", False, None),
    Tweet("syn-011", "Rain started the second I took the laundry outside. of course it did", "2025-01-10T16:25:00Z", "twitter", True, "conv-011"),
    Tweet("syn-012", "Somebody's dog on the bus had a better morning than all of us 🐶", "2025-01-11T09:35:00Z", "twitter", False, None),
    Tweet("syn-013", "My calendar reminder says 'drink water' like I haven't been ignoring it all day 🙃", "2025-01-12T18:00:00Z", "twitter", False, "conv-013"),
    Tweet("syn-014", "I opened the fridge for answers and it offered me cheese.", "2025-01-13T21:15:00Z", "twitter", False, None),
    Tweet("syn-015", "Me: I'll just check one notification. Also me, 45 minutes later:", "2025-01-14T22:10:00Z", "twitter", True, "conv-015"),
)