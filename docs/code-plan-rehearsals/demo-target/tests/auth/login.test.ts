import assert from "node:assert/strict";
import test from "node:test";

import { loginRoute } from "../../src/routes/auth";

test("loginRoute returns token for valid credentials", async () => {
  const response = await loginRoute({
    email: "dev@example.com",
    password: "secret",
  });

  assert.equal(response.status, 200);
  assert.deepEqual(response.body, {
    token: "token:user-1",
  });
});

test("loginRoute currently throws when repository returns null", async () => {
  await assert.rejects(async () => {
    await loginRoute({
      email: "missing@example.com",
      password: "secret",
    });
  });
});
