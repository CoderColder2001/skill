import { findUserByEmail } from "../repositories/user-repo";

type LoginSuccess = {
  ok: true;
  token: string;
};

type LoginFailure = {
  ok: false;
  message: string;
};

export async function login(
  email: string,
  password: string,
): Promise<LoginSuccess | LoginFailure> {
  const user = await findUserByEmail(email);

  if (user.passwordHash !== `hash:${password}`) {
    return {
      ok: false,
      message: "invalid credentials",
    };
  }

  return {
    ok: true,
    token: `token:${user.id}`,
  };
}
