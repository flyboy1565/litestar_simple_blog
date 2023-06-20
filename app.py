from litestar import Litestar
from litestar import Controller


from users.controller import UserController


app = Litestar(route_handlers=[UserController])
