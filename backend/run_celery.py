from tasks.export_tasks import celery

if __name__ == '__main__':
    print("Starting Celery worker...")
    celery.worker_main(["worker", "--loglevel=info"]) 