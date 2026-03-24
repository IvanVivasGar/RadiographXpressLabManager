# WebSockets and Real-time Updates

RadiographXpress relies heavily on WebSockets to build a responsive, concurrent experience for Radiologists and Patients. This is achieved using **Django Channels**.

## Architecture Setup

Django Channels replaces the standard Django WSGI interface with an **ASGI** (Asynchronous Server Gateway Interface) router.

1.  **Server:** `daphne` handles all incoming HTTP/WS traffic on port 8000.
2.  **Router:** `radiographxpress/asgi.py` routes standard HTTP requests to Django's normal views, and upgrades `/ws/` requests to WebSockets via `AuthMiddlewareStack`.
3.  **Channel Layer:** The message broker that allows different instances of Daphne (or background processes) to talk to the WebSocket connections.
    *   **Local Dev:** Uses `InMemoryChannelLayer`.
    *   **Production:** Uses `channels_redis.core.RedisChannelLayer` connected to a Redis container.

## The `StudyConsumer` (`core/consumers.py`)

The main WebSocket consumer is `StudyConsumer`. It handles real-time updates regarding the state of `Study` objects.

### Connection & Groups
When a client (usually javascript on the patient or doctor dashboard) connects via `new WebSocket('ws://host/ws/notifications/')`, the consumer:
1.  Accepts the connection (`self.accept()`).
2.  Adds the connection to a global Django Channels group named `"notifications"`.

```python
async def connect(self):
    await self.channel_layer.group_add("notifications", self.channel_name)
    await self.accept()
```

### Broadcasting Events

When a radiologist "locks" a study to begin interpreting it, the system needs to immediately update the UI of all other logged-in doctors to show that study as "In Progress" (preventing duplicate work) and update the Patient's UI to show their study is currently being reviewed.

This broadcast happens in the standard Django Views (e.g., `doctorsDashboard/views.py`), not inside the consumer, using the `channel_layer`.

**Example: Broadcasting a Lock Event:**
```python
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def lock_study_view(request, study_id):
    # ... logic to assign locked_by = request.user.reportingdoctor ...
    
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "notifications", 
        {
            "type": "study_update", # Maps to the study_update method in consumers.py
            "message": {
                "study_id": study_id,
                "status": "In Progress"
            }
        }
    )
```

### Receiving on the Frontend

The client-side JavaScript listens to the `onmessage` event:

```javascript
const socket = new WebSocket('ws://' + window.location.host + '/ws/notifications/');

socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    // If data.study_id matches a study card on the screen, 
    // update the UI (change icon to lock, disable button, show "In Progress").
};
```

## Developer Guidelines for Async/Sync

*   **Django ORM is Synchronous:** Be very careful querying the database inside a `WebsocketConsumer` method. If you must hit the database, wrap the call in `@database_sync_to_async`.
*   **Calling Channels from Views:** Django views are synchronous. You must use `asgiref.sync.async_to_sync()` when calling `channel_layer.group_send` from inside a normal view.
*   **Data Serialization:** Always serialize data to strings/JSON before pushing it onto the channel layer. Complex Python objects (like Django QuerySets or Model Instances) cannot be serialized by Redis.
