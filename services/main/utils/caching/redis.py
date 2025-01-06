import redis
from dotenv import load_dotenv
load_dotenv()

redis = redis.Redis(host='localhost', port=6379, decode_responses=True, )

# redis = redis.Redis(
#     host=os.environ.get("REDIS_HOST"),
#     port=12326,
#     decode_responses=True,
#     username="default",
#     password=os.environ.get("REDIS_PASSWORD"),
# )


