import axios from "axios";
const api = axios.create({
  baseURL: process.env.TRUVERA_API || "https://api-testnet.truvera.io",
  headers: {
    Authorization: `Bearer ${process.env.TRUVERA_JWT}`,
    "Content-Type": "application/json",
    Accept: "*/*",
  },
});

export default api;
