import { useEffect, useState } from "react"
import { Link } from "react-router-dom"

interface PageItem {
  id: number
  slug: string
  title: string
  is_public: boolean
  updated_at: string
}

function loadPages(
  setPages: (d: PageItem[]) => void,
  setError: (e: string | null) => void,
  setLoading: (l: boolean) => void,
) {
  setLoading(true)
  fetch("/api/pages/")
    .then((res) => {
      if (!res.ok) throw new Error("Error al cargar páginas")
      return res.json()
    })
    .then((data) => {
      setPages(data)
      setError(null)
    })
    .catch((err) => setError(err.message))
    .finally(() => setLoading(false))
}

export default function Pages() {
  const [pages, setPages] = useState<PageItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadPages(setPages, setError, setLoading)
  }, [])

  const refresh = () => loadPages(setPages, setError, setLoading)

  const handleDelete = (id: number, slug: string) => {
    if (!window.confirm(`¿Eliminar la página "${slug}"? Esta acción no se puede deshacer.`)) return
    fetch(`/api/pages/${id}/`, { method: "DELETE" })
      .then((res) => {
        if (res.ok) refresh()
        else setError("Error al eliminar")
      })
      .catch(() => setError("Error al eliminar"))
  }

  if (loading) return <p className="p-6 text-gray-600">Cargando páginas…</p>
  if (error) return <p className="p-6 text-red-600">Error: {error}</p>

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-semibold text-gray-800">Páginas de contenido</h1>
        <Link
          to="/pages/new"
          className="px-4 py-2 bg-blue-600 text-white rounded font-medium hover:bg-blue-700"
        >
          Nueva página
        </Link>
      </div>
      <div className="overflow-x-auto rounded-lg border border-gray-200">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">
                Slug
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">
                Título
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">
                Pública
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">
                Actualizada
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {pages.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                  No hay páginas creadas.
                </td>
              </tr>
            ) : (
              pages.map((p) => (
                <tr key={p.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm text-gray-700">{p.slug}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">{p.title}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">
                    {p.is_public ? "Sí" : "No"}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">
                    {new Date(p.updated_at).toLocaleString()}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-x-3 gap-y-1">
                      <Link
                        to={`/pages/${p.id}/edit`}
                        className="text-blue-600 hover:underline text-sm font-medium"
                      >
                        Editar
                      </Link>
                      <button
                        type="button"
                        onClick={() => handleDelete(p.id, p.slug)}
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

