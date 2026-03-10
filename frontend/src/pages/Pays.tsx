import { useEffect, useState } from "react"

interface PayItem {
  id: number
  code: string
  meet_id: number | null
  therapist_name: string
  patient_name: string
  amount: string
  status: string
  timestamp: string
}

function loadPays(
  setPays: (d: PayItem[]) => void,
  setError: (e: string | null) => void,
  setLoading: (l: boolean) => void,
) {
  setLoading(true)
  fetch("/api/pays/")
    .then((res) => {
      if (!res.ok) throw new Error("Error al cargar pagos")
      return res.json()
    })
    .then((data) => {
      setPays(data)
      setError(null)
    })
    .catch((err) => setError(err.message))
    .finally(() => setLoading(false))
}

export default function Pays() {
  const [pays, setPays] = useState<PayItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadPays(setPays, setError, setLoading)
  }, [])

  const refresh = () => loadPays(setPays, setError, setLoading)

  const handleConfirm = (id: number) => {
    fetch(`/api/pays/${id}/confirm/`, { method: "POST" })
      .then((res) => (res.ok ? res.json() : Promise.reject()))
      .then(() => refresh())
      .catch(() => setError("Error al confirmar pago"))
  }

  const handleDelete = (id: number, code: string) => {
    if (!window.confirm(`¿Eliminar el pago ${code}? Esta acción no se puede deshacer.`)) return
    fetch(`/api/pays/${id}/`, { method: "DELETE" })
      .then((res) => {
        if (res.ok) refresh()
        else setError("Error al eliminar")
      })
      .catch(() => setError("Error al eliminar"))
  }

  if (loading) return <p className="p-6 text-gray-600">Cargando pagos…</p>
  if (error) return <p className="p-6 text-red-600">Error: {error}</p>

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-semibold text-gray-800">Pagos</h1>
      </div>
      <div className="overflow-x-auto rounded-lg border border-gray-200">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">
                Código
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">
                Cita
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">
                Terapeuta
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">
                Paciente
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">
                Importe
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">
                Estado
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">
                Fecha
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {pays.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-4 py-8 text-center text-gray-500">
                  No hay pagos registrados.
                </td>
              </tr>
            ) : (
              pays.map((p) => (
                <tr key={p.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm text-gray-700">{p.code}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">
                    {p.meet_id ? `Cita #${p.meet_id}` : "—"}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-700">{p.therapist_name}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">{p.patient_name}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">{p.amount}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">{p.status}</td>
                  <td className="px-4 py-3 text-sm text-gray-500">
                    {new Date(p.timestamp).toLocaleString()}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-x-3 gap-y-1">
                      {p.status !== "D" && (
                        <button
                          type="button"
                          onClick={() => handleConfirm(p.id)}
                          className="text-green-600 hover:underline text-sm font-medium"
                        >
                          Marcar pagado
                        </button>
                      )}
                      <button
                        type="button"
                        onClick={() => handleDelete(p.id, p.code)}
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

