import uvicorn
import threading

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from db.database import SessionLocal
from apis.auth import auth_app
from apis.todo import todo_app
from controllers.blacklist import create_blacklist_token
from utils.db import get_db
from utils.jwt import get_current_user_token, get_current_user_email
from utils.error import print_error, CREDENTIALS_EXCEPTION
from utils.scheduler import scheduler
from utils.env_loader import APP_URL


app = FastAPI()

ALLOWED_HOSTS = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        if (
            request.url.path != "/"
            and request.url.path != "/token"
            and request.url.path.find("/auth/") == -1
        ):
            token: str = await get_current_user_token(request)
            email: str = await get_current_user_email(request)
            request.state.user_token = token
            request.state.user_email = email
        response = await call_next(request)
    except Exception as e:
        print_error("Credentials Exception", e)
        response = JSONResponse(
            {
                "detail": "Could not validate credentials",
            },
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    finally:
        request.state.db.close()
    return response


app.mount("/auth", auth_app)
app.mount("/api", todo_app)


@app.get("/")
async def root():
    return HTMLResponse('<body><a href="/auth/login">Log In</a></body>')


@app.get("/token")
async def token(request: Request):
    return HTMLResponse(
        """
            <script>
                function send(){
                    var req = new XMLHttpRequest();
                    req.onreadystatechange = function() {
                        if (req.readyState === 4) {
                            console.log(req.response);
                            if (req.response["result"] === true) {
                                window.localStorage.setItem('jwt', req.response["access_token"]);
                                window.localStorage.setItem('refresh', req.response["refresh_token"]);
                            }
                        }
                    }
                    req.withCredentials = true;
                    req.responseType = 'json';
                    req.open("get", "/auth/token?"+window.location.search.substr(1), true);
                    req.send("");
                }
            </script>
            <button onClick="send()">Get FastAPI JWT Token</button>
            <button onClick='fetch("{APP_URL}/logout",{
                headers:{
                    "Authorization": "Bearer " + window.localStorage.getItem("jwt")
                },
            }).then((r)=>r.json()).then((msg)=>{
                console.log(msg);
                if (msg["result"] === true) {
                    window.localStorage.removeItem("jwt");
                }
                });'>
            Logout
            </button>
            <button onClick='fetch("{APP_URL}/auth/refresh",{
                method: "POST",
                headers:{
                    "Authorization": "Bearer " + window.localStorage.getItem("jwt")
                },
                body:JSON.stringify({
                    grant_type:\"refresh_token\",
                    refresh_token:window.localStorage.getItem(\"refresh\")
                })
            }).then((r)=>r.json()).then((msg)=>{
                console.log(msg);
                if (msg["result"] === true) {
                    window.localStorage.setItem("jwt", msg["access_token"]);
                }
                });'>
            Refresh
            </button>
        """
    )


@app.get("/logout")
async def logout(request: Request):
    try:
        token: str = request.state.user_token
        db = get_db(request)
        db_blacklist = create_blacklist_token(db, token)
        if db_blacklist:
            return JSONResponse({"result": True})
    except Exception as e:
        print_error("Try Logout", e)
        raise CREDENTIALS_EXCEPTION

    print_error("Logout Error", "Something went wrong")
    raise CREDENTIALS_EXCEPTION


if __name__ == "__main__":
    scheduler_thread = threading.Thread(target=scheduler)
    scheduler_thread.start()
    uvicorn.run(app, port=8000, host="0.0.0.0")
