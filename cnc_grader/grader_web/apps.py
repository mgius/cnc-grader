from django.apps import AppConfig

class GraderConfig(AppConfig):
    name = 'cnc_grader.grader_web'
    def ready(self):
        # import the tasks so that the receiver gets registered
        import cnc_grader.docker_worker.tasks

    
