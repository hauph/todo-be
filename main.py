import uvicorn
from fastapi import FastAPI, Request, Depends, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from db.database import SessionLocal

from apis.auth import auth_app

from apis.todo import todo_app
from controllers.blacklist import create_blacklist_token
from utils.db import get_db
from utils.jwt import get_current_user_token
from utils.error import print_error, CREDENTIALS_EXCEPTION


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
        response = await call_next(request)
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
                <button onClick='fetch("http://127.0.0.1:7000/api/").then(
                    (r)=>r.json()).then((msg)=>{console.log(msg)});'>
                Call Unprotected API
                </button>
                <button onClick='fetch("http://127.0.0.1:7000/api/protected").then(
                    (r)=>r.json()).then((msg)=>{console.log(msg)});'>
                Call Protected API without JWT
                </button>
                <button onClick='fetch("http://127.0.0.1:7000/api/protected",{
                    headers:{
                        "Authorization": "Bearer " + window.localStorage.getItem("jwt")
                    },
                }).then((r)=>r.json()).then((msg)=>{console.log(msg)});'>
                Call Protected API wit JWT
                </button>
                <button onClick='fetch("http://127.0.0.1:7000/logout",{
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
                <button onClick='fetch("http://127.0.0.1:7000/auth/refresh",{
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
        token: str = await get_current_user_token(request)
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
    uvicorn.run(app, port=7000)
