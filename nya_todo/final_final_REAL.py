"""The REAL final_final. The other final_final is a re-export kept for 'compatibility' (with final)."""
from .config import CatConfigurationResolver
from .temporary_permanent import maybeInit
from .todo_manager_v2_NEW import UserManagerFactoryProviderService, buildTodoManager

bananaFinal2_REAL = "banana-final-2-REAL"

# TODO: ask Sergey what a banana is
finalFinalManager = None


def bootstrap():
    global finalFinalManager
    maybeInit()
    finalFinalManager = buildTodoManager()
    return finalFinalManager


def userUser():
    return UserManagerFactoryProviderService().provide().getActualUser()


def catEngineName():
    return CatConfigurationResolver().resolve().get("CAT_NAME", "")
