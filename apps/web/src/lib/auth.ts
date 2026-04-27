const TOKEN_KEY = "token";
const REFRESH_KEY = "refreshToken";
const USER_KEY = "userId";

export const auth = {
  getToken: () => localStorage.getItem(TOKEN_KEY),

  setSession: (data: {
    access_token: string;
    refresh_token: string;
    user_id: string;
    username: string;
  }) => {
    localStorage.setItem(TOKEN_KEY, data.access_token);
    localStorage.setItem(REFRESH_KEY, data.refresh_token);
    localStorage.setItem(USER_KEY, data.user_id);
    localStorage.setItem("username", data.username);
  },

  clear: () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem(USER_KEY);
    localStorage.removeItem("username");
  },

  isLoggedIn: () => {
    return !!localStorage.getItem(TOKEN_KEY);
  },
};