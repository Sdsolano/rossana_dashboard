import { useEffect, useState } from "react"
import { Link } from "react-router-dom"

interface PatientItem {
  id: number
  username: string
  first_name: string
  last_name: string
  email: string
  is_active: boolean
  telephone: string
  timezone_verbose: string
}

function loadPatients(
  setPatients: (d: PatientItem[]) => void,
  setError: (e: string | null) => void,
  setLoading: (l: boolean) => void,
) {
  setLoading(true)
  fetch("/api/patients/")
    .then((res) => {
      if (!res.ok) throw new Error("Error al cargar pacientes")
      return res.json()
    })
    .then((data) => {
      setPatients(data)
      setError(null)
    })
    .catch((err) => setError(err.message))
    .finally(() => setLoading(false))
}

export default function Patients() {
  const [patients, setPatients] = useState<PatientItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadPatients(setPatients, setError, setLoading)
  }, [])

  const refresh = () => loadPatients(setPatients, setError, setLoading)

  const handleActivate = (id: number) => {
    fetch(`/api/patients/${id}/activate/`, { method: "POST" })
      .then((res) => (res.ok ? res.json() : Promise.reject()))
      .then((updated) => {
        setPatients((prev) => prev.map((p) => (p.id === id ? updated : p)))
      })
      .catch(() => setError("Error al activar"))
  }

  const handleDeactivate = (id: number) => {
    fetch(`/api/patients/${id}/deactivate/`, { method: "POST" })
      .then((res) => (res.ok ? res.json() : Promise.reject()))
      .then((updated) => {
        setPatients((prev) => prev.map((p) => (p.id === id ? updated : p)))
      })
      .catch(() => setError("Error al desactivar"))
  }

  const handleDelete = (id: number, username: string) => {
    if (!window.confirm(`¿Eliminar al paciente "${username}"? Esta acción no se puede deshacer.`)) return
    fetch(`/api/patients/${id}/`, { method: "DELETE" })
      .then((res) => {
        if (res.ok) refresh()
        else setError("Error al eliminar")
      })
      .catch(() => setError("Error al eliminar"))
  }

  if (loading) return <p className="p-6 text-gray-600">Cargando pacientes…</p>
  if (error) return <p className="p-6 text-red-600">Error: {error}</p>

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-semibold text-gray-800">Pacientes</h1>
        <Link
          to="/patients/new"
          className="px-4 py-2 bg-blue-600 text-white rounded font-medium hover:bg-blue-700"
        >
          Agregar paciente
        </Link>
      </div>
      <div className="overflow-x-auto rounded-lg border border-gray-200">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">#</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">Usuario</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">Nombre</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">Apellido</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">Email</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">Teléfono</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">Zona horaria</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">Activo</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">Acciones</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {patients.length === 0 ? (
              <tr>
                <td colSpan={9} className="px-4 py-8 text-center text-gray-500">
                  No hay pacientes registrados.
                </td>
              </tr>
            ) : (
              patients.map((p) => (
                <tr key={p.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm text-gray-700">{p.id}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">{p.username}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">{p.first_name}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">{p.last_name}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">{p.email}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">{p.telephone}</td>
                  <td className="px-4 py-3 text-sm text-gray-600">{p.timezone_verbose}</td>
                  <td className="px-4 py-3">
                    <span
                      className={p.is_active ? "text-green-600 font-medium" : "text-gray-400"}
                    >
                      {p.is_active ? "Sí" : "No"}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-x-3 gap-y-1">
                      <Link
                        to={`/patients/${p.id}/edit`}
                        className="text-blue-600 hover:underline text-sm font-medium"
                      >
                        Editar
                      </Link>
                      {p.is_active ? (
                        <button
                          type="button"
                          onClick={() => handleDeactivate(p.id)}
                          className="text-amber-600 hover:underline text-sm"
                        >
                          Desactivar
                        </button>
                      ) : (
                        <button
                          type="button"
                          onClick={() => handleActivate(p.id)}
                          className="text-green-600 hover:underline text-sm font-medium"
                        >
                          Activar
                        </button>
                      )}
                      <button
                        type="button"
                        onClick={() => handleDelete(p.id, p.username)}
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

