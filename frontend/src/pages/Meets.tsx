import { useEffect, useState } from "react"
import { Link } from "react-router-dom"

interface MeetItem {
  id: number
  therapist_id: number
  patient_id: number | null
  patient_name: string
  date: string
  number: number
  status: string
}

function loadMeets(
  setMeets: (d: MeetItem[]) => void,
  setError: (e: string | null) => void,
  setLoading: (l: boolean) => void,
) {
  setLoading(true)
  fetch("/api/meets/")
    .then((res) => {
      if (!res.ok) throw new Error("Error al cargar citas")
      return res.json()
    })
    .then((data) => {
      setMeets(data)
      setError(null)
    })
    .catch((err) => setError(err.message))
    .finally(() => setLoading(false))
}

export default function Meets() {
  const [meets, setMeets] = useState<MeetItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadMeets(setMeets, setError, setLoading)
  }, [])

  if (loading) return <p className="p-6 text-gray-600">Cargando citas…</p>
  if (error) return <p className="p-6 text-red-600">Error: {error}</p>

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-semibold text-gray-800">Citas</h1>
        <Link
          to="/meets/book"
          className="px-4 py-2 bg-blue-600 text-white rounded font-medium hover:bg-blue-700"
        >
          Reservar cita
        </Link>
      </div>
      <div className="overflow-x-auto rounded-lg border border-gray-200">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">#</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">Terapeuta</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">Fecha</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">Slot</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">Paciente</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">Estado</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">Acciones</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {meets.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-gray-500">
                  No hay citas generadas. Usa &quot;Generar agenda&quot; en Terapeutas.
                </td>
              </tr>
            ) : (
              meets.map((m) => (
                <tr key={m.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm text-gray-700">{m.id}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">{m.therapist_id}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">{m.date}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">{m.number}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">
                    {m.patient_name || (m.patient_id ? `#${m.patient_id}` : "—")}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-700">{m.status}</td>
                  <td className="px-4 py-3">
                    <Link
                      to={`/meets/${m.id}/edit`}
                      className="text-blue-600 hover:underline text-sm font-medium"
                    >
                      Editar
                    </Link>
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

