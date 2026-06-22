import { login } from "../services/auth-service";

export async function loginRoute(request: {
  email?: string;
  password?: string;
}) {
  const result = await login(request.email ?? "", request.password ?? "");

  if (!result.ok) {
    return {
      status: 500,
      body: {
        code: "LOGIN_FAILED",
        message: result.message,
      },
    };
  }

  return {
    status: 200,
    body: {
      token: result.token,
    },
  };
}
