import { useEffect, useState } from "react"
import { Link } from "react-router-dom"

export interface TherapistItem {
  id: number
  username: string
  first_name: string
  last_name: string
  email: string
  is_active: boolean
  timezone_verbose: string
}

function loadTherapists(setTherapists: (d: TherapistItem[]) => void, setError: (e: string | null) => void, setLoading: (l: boolean) => void) {
  setLoading(true)
  fetch("/api/therapists/")
    .then((res) => {
      if (!res.ok) throw new Error("Error al cargar terapeutas")
      return res.json()
    })
    .then((data) => {
      setTherapists(data)
      setError(null)
    })
    .catch((err) => setError(err.message))
    .finally(() => setLoading(false))
}

export default function Therapists() {
  const [therapists, setTherapists] = useState<TherapistItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadTherapists(setTherapists, setError, setLoading)
  }, [])

  const refresh = () => loadTherapists(setTherapists, setError, setLoading)

  const handleActivate = (id: number) => {
    fetch(`/api/therapists/${id}/activate/`, { method: "POST" })
      .then((res) => res.ok ? res.json() : Promise.reject())
      .then((updated) => {
        setTherapists((prev) => prev.map((t) => (t.id === id ? updated : t)))
      })
      .catch(() => setError("Error al activar"))
  }

  const handleDeactivate = (id: number) => {
    fetch(`/api/therapists/${id}/deactivate/`, { method: "POST" })
      .then((res) => res.ok ? res.json() : Promise.reject())
      .then((updated) => {
        setTherapists((prev) => prev.map((t) => (t.id === id ? updated : t)))
      })
      .catch(() => setError("Error al desactivar"))
  }

  const handleDelete = (id: number, username: string) => {
    if (!window.confirm(`¿Eliminar al terapeuta "${username}"? Esta acción no se puede deshacer.`)) return
    fetch(`/api/therapists/${id}/`, { method: "DELETE" })
      .then((res) => {
        if (res.ok) refresh()
        else setError("Error al eliminar")
      })
      .catch(() => setError("Error al eliminar"))
  }

  const handleGenerateSchedule = (id: number) => {
    fetch(`/api/therapists/${id}/generate-schedule/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ days: 3 }),
    })
      .then((r) => r.json())
      .then((data) => alert(data.detail || "Agenda generada."))
      .catch(() => setError("Error al generar agenda"))
  }

  if (loading) return <p className="p-6 text-gray-600">Cargando terapeutas…</p>
  if (error) return <p className="p-6 text-red-600">Error: {error}</p>

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-semibold text-gray-800">Terapeutas</h1>
        <Link
          to="/therapists/new"
          className="px-4 py-2 bg-blue-600 text-white rounded font-medium hover:bg-blue-700"
        >
          Agregar terapeuta
        </Link>
      </div>
      <div className="overflow-x-auto rounded-lg border border-gray-200">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">
                #
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">
                Usuario
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">
                Nombre
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">
                Apellido
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">
                Email
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">
                Activo
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">
                Zona horaria
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {therapists.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-4 py-8 text-center text-gray-500">
                  No hay terapeutas registrados.
                </td>
              </tr>
            ) : (
              therapists.map((t) => (
                <tr key={t.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm text-gray-700">{t.id}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">
                    {t.username}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-700">
                    {t.first_name}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-700">
                    {t.last_name}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-700">{t.email}</td>
                  <td className="px-4 py-3">
                    <span
                      className={
                        t.is_active
                          ? "text-green-600 font-medium"
                          : "text-gray-400"
                      }
                    >
                      {t.is_active ? "Sí" : "No"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {t.timezone_verbose}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-x-3 gap-y-1">
                    <Link
                      to={`/therapists/${t.id}/edit`}
                      className="text-blue-600 hover:underline text-sm font-medium"
                    >
                      Editar
                    </Link>
                    <Link
                      to={`/therapists/${t.id}/password`}
                      className="text-gray-600 hover:underline text-sm"
                    >
                      Contraseña
                    </Link>
                    {t.is_active ? (
                      <button
                        type="button"
                        onClick={() => handleDeactivate(t.id)}
                        className="text-amber-600 hover:underline text-sm"
                      >
                        Desactivar
                      </button>
                    ) : (
                      <button
                        type="button"
                        onClick={() => handleActivate(t.id)}
                        className="text-green-600 hover:underline text-sm font-medium"
                      >
                        Activar
                      </button>
                    )}
                    <button
                      type="button"
                      onClick={() => handleGenerateSchedule(t.id)}
                      className="text-green-600 hover:underline text-sm"
                    >
                      Generar agenda
                    </button>
                    <button
                      type="button"
                      onClick={() => handleDelete(t.id, t.username)}
                      className="text-red-600 hover:underline text-sm"
                    >
                      Eliminar
                    </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
