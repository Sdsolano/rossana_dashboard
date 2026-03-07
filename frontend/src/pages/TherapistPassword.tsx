import { useState } from "react"
import { useNavigate, useParams } from "react-router-dom"

export default function TherapistPassword() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [password, setPassword] = useState("")
  const [password_confirm, setPassword_confirm] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Record<string, string[]>>({})

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!id) return
    setLoading(true)
    setError({})
    fetch(`/api/therapists/${id}/password/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password, password_confirm }),
    })
      .then((res) => res.json().then((data) => ({ status: res.status, data })))
      .then(({ status, data }) => {
        if (status === 200) {
          navigate("/therapists")
          return
        }
        if (status === 400 && typeof data === "object") setError(data)
      })
      .finally(() => setLoading(false))
  }

  return (
    <div className="p-6 max-w-md mx-auto">
      <h1 className="text-2xl font-semibold text-gray-800 mb-6">Cambiar contraseña</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Nueva contraseña *</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full border border-gray-300 rounded px-3 py-2"
            required
          />
          {error.password && <p className="text-red-600 text-sm mt-1">{error.password[0]}</p>}
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Repetir contraseña *</label>
          <input
            type="password"
            value={password_confirm}
            onChange={(e) => setPassword_confirm(e.target.value)}
            className="w-full border border-gray-300 rounded px-3 py-2"
            required
          />
          {error.password_confirm && <p className="text-red-600 text-sm mt-1">{error.password_confirm[0]}</p>}
        </div>
        <div className="flex gap-3 pt-2">
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "Guardando…" : "Guardar"}
          </button>
          <button
            type="button"
            onClick={() => navigate("/therapists")}
            className="px-4 py-2 border border-gray-300 rounded font-medium text-gray-700 hover:bg-gray-50"
          >
            Cancelar
          </button>
        </div>
      </form>
    </div>
  )
}
