from fastapi import FastAPI, Request, Depends, HTTPException
from typing import Callable
from fastapi.responses import JSONResponse
from functools import wraps


def log_around_execution(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get("request")
        
        if request:
            print(f"Before API execution: Path={request.url.path}, Method={request.method}")
        else:
            print("Before API execution")

        response = await func(*args, **kwargs)

        print(f"After API execution: Response={response}")
        return response
    return wrapper