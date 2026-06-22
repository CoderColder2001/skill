type UserRecord = {
  id: string;
  email: string;
  passwordHash: string;
};

const users: Record<string, UserRecord> = {
  "dev@example.com": {
    id: "user-1",
    email: "dev@example.com",
    passwordHash: "hash:secret",
  },
};

export async function findUserByEmail(
  email: string,
): Promise<UserRecord | null> {
  return users[email] ?? null;
}
