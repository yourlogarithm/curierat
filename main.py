from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import packages_router, routes_router, transports_router, users_router, authentication_router

app = FastAPI()

app.include_router(packages_router.PackagesRouter.router)
app.include_router(routes_router.RoutesRouter.router)
app.include_router(transports_router.TransportsRouter.router)
app.include_router(users_router.UsersRouter.router)
app.include_router(authentication_router.AuthenticationRouter.router)

origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
