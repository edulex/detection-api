import threading
from queue import Queue
from typing import Dict, Callable, List


def get_queued_tasks() -> Dict[str, List[str]]:
    """Get a snapshot of all queued tasks for each user."""
    snapshot = {}
    for user_id, queue in user_queues.items():
        snapshot[user_id] = list(queue.queue)  # Convert queue to a list for easier inspection
    return snapshot


# Global dictionary to hold queues for each user
user_queues: Dict[str, Queue] = {}

# Locks for each user to prevent concurrent processing
user_locks: Dict[str, threading.Lock] = {}

def add_task_to_queue(user_id: str, task: Callable):
    """Add a task to the user's queue and start processing if not already running."""
    if user_id not in user_queues:
        user_queues[user_id] = Queue()
        user_locks[user_id] = threading.Lock()

    # Add the task to the user's queue
    user_queues[user_id].put(task)

    # Start processing if no other tasks are running
    thread = threading.Thread(target=process_user_queue, args=(user_id,))
    thread.start()

def process_user_queue(user_id: str):
    """Process tasks from the user's queue one at a time."""
    with user_locks[user_id]:  # Ensure only one thread processes the user's queue at a time
        queue = user_queues[user_id]
        while not queue.empty():
            task = queue.get()
            try:
                task()
            except Exception as e:
                print(f"Error processing task for user {user_id}: {e}")
