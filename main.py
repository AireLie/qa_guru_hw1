from fastapi import FastAPI, HTTPException
import json

app = FastAPI()

with open("data.json", "r") as read_file:
    users = json.load(read_file)


def save_users():
    with open("data.json", "w") as write_file:
        json.dump(users, write_file)


@app.get("/api/users/{user_id}")
def get_user(user_id: int):
    user_id = str(user_id)
    if user_id in users:
        return users[user_id]
    else:
        raise HTTPException(status_code=404, detail="User not found")


@app.post("/api/users")
def create_user(user: dict):
    user_id = str(user['id'])
    users[user_id] = user
    save_users()
    return user


@app.put("/api/users/{user_id}")
def update_user(user_id: int, user: dict):
    user_id = str(user_id)
    if user_id in users:
        users[user_id] = user
        save_users()
        return users[user_id]
    else:
        raise HTTPException(status_code=404, detail="User not found")


@app.delete("/api/users/{user_id}")
def delete_user(user_id: int):
    user_id = str(user_id)
    if user_id in users:
        del users[user_id]
        save_users()
        return {"message": f"User {user_id} deleted"}
    else:
        raise HTTPException(status_code=404, detail="User not found")


@app.post("/api/login")
def login(data: dict):
    if data.get("email") == "eve.holt@reqres.in" and data.get("password") == "cityslicka":
        return {"token": "QpwL5tke4Pnpja7X4"}
    else:
        raise HTTPException(status_code=401, detail="Bad credentials")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
