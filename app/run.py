# In a script or shell
from app.database import engine
from app.models import user  # imports the model
user.Base.metadata.create_all(bind=engine)
