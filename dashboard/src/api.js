const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function fetchDashboardData() {
  const response = await fetch(`${API_URL}/dashboard-data`);

  if (!response.ok) {
    throw new Error(`Erro ao consultar a API (status ${response.status})`);
  }

  return response.json();
}
