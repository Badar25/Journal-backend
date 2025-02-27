
# Dating App Backend 

A NestJS-based dating application API that handles user profiles, likes, and matches.

## Features

- User Management
  - Create user profiles (No Auth etc, simple register)
  - Get user details
  - List all users
- Match System
  - Like other users
  - Automatic match creation when both users like each other
  - Match history tracking


## Installation

1. Clone the repository:
```bash
git clone https://github.com/Badar25/dating-app-backend.git
cd simple-app
```

2. Install dependencies:
```bash
npm install
```

3. Start MongoDB:
```bash
mongod
```

4. Start the application:
```bash
npm run start:dev
```

## API Endpoints

### User Endpoints

- `POST /user/create` - Create a new user
  ```json
  {
    "name": "string",
    "imageUrl": "string"
  }
  ```

- `GET /user` - Get all users
- `GET /user/:id` - Get user by ID

### Match Endpoints

- `POST /match/like` - Like a user
  ```json
  {
    "userA": "string (userId)",
    "userB": "string (userId)"
  }
  ```

## Database Schema

### User Collection
- name: string
- imageUrl: string (optional)

### Like Collection
- userId: ObjectId
- likedUserId: ObjectId

### Match Collection
- users: [ObjectId] (sorted array of two user IDs)

## Error Handling

The API includes some error handling (not all) for:
- Invalid user IDs
- Self-liking prevention
- Duplicate likes
- Duplicate matches
- Non-existent users

## Development

To run the application in development mode:

```bash
npm run start:dev
```

The API will be available at `http://localhost:3000`


## Project Structure

```
src/
├── user/
│   ├── schemas/
│   ├── user.controller.ts
│   ├── user.module.ts
│   └── user.service.ts
├── match/
│   ├── schemas/
│   ├── match.controller.ts
│   ├── match.module.ts
│   └── match.service.ts
└── app.module.ts
```