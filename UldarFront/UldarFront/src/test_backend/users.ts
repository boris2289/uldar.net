export interface Users {
  id: number,
  first_name: string,
  second_name: string,
  username: string,
  email: string,
  bio: string,
  avatar: string
}

export let users_list = [
  {
    "id": 1,
    "first_name": 'Bob',
    "second_name": 'Marley',
    "username": 'bob_marley',
    "email": 'bob@email.com',
    "bio": 'newbie coder)',
    "avatar": "https://ui-avatars.com/api/?name=Bob+marley"
  },
  {
    id: 2,
    first_name: 'Dean',
    second_name: 'Winchester',
    username: 'dean_impala',
    email: 'dean@email.com',
    bio: 'supernatural killer)',
    avatar: "https://ui-avatars.com/api/?name=Dean+Winchester"
  },
  {
    id: 3,
    first_name: 'Sam',
    second_name: 'Winchester',
    username: 'sammy',
    email: 'sam@email.com',
    bio: 'hate supernatural',
    avatar: "https://ui-avatars.com/api/?name=Sam+Winchester"
  },
]
