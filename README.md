# The Crash and Compile Automated Grader

After multiple iterations by multiple people, it's now my turn to take a crack
at this. A grader for crash and compile (or any programming contest really).

Implemented with Django, Celery, and Docker.  Suprisingly little code for the
service it provides.

Assumes that the user running django will have access to the docker service
without a password, not currently configurable.

Uses redis as a celery task queue.  Fortunately, docker has an official redis
instance you can spin up (dockerfile/redis).  Uses docker for test isolation.

For supported languages see
cnc_grader/docker_worker/docker_exectuor/test_executor.py
