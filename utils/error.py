from fastapi import HTTPException, status


def print_error(title: str, des: str):
    print(f"========{title}========")
    print(des if des is not None else "")


# Error
CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
