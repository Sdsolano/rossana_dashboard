import { useState } from "react"
import { useNavigate } from "react-router-dom"

export default function PageNew() {
  const navigate = useNavigate()
  const [slug, setSlug] = useState("")
  const [title, setTitle] = useState("")
  const [body, setBody] = useState("")
  const [is_public, setIsPublic] = useState(true)
  const [submitLoading, setSubmitLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [formError, setFormError] = useState<Record<string, string[]>>({})

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setFormError({})
    setSubmitLoading(true)
    fetch("/api/pages/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        slug,
        title,
        body,
        is_public,
      }),
    })
      .then((r) => r.json().then((data) => ({ status: r.status, data })))
      .then(({ status, data }) => {
        if (status === 201) {
          navigate("/pages")
          return
        }
        if (status === 400 && typeof data === "object") setFormError(data)
        else setError("Error al crear página")
      })
      .catch(() => setError("Error de conexión"))
      .finally(() => setSubmitLoading(false))
  }

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-semibold text-gray-800 mb-6">Nueva página</h1>
      {error && <p className="mb-4 text-red-600 text-sm">{error}</p>}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Slug *</label>
          <input
            type="text"
            value={slug}
            onChange={(e) => setSlug(e.target.value)}
            className="w-full border border-gray-300 rounded px-3 py-2"
            required
          />
          {formError.slug && (
            <p className="text-red-600 text-sm mt-1">{formError.slug[0]}</p>
          )}
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Título *</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full border border-gray-300 rounded px-3 py-2"
            required
          />
          {formError.title && (
            <p className="text-red-600 text-sm mt-1">{formError.title[0]}</p>
          )}
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Contenido</label>
          <textarea
            value={body}
            onChange={(e) => setBody(e.target.value)}
            className="w-full border border-gray-300 rounded px-3 py-2 h-48"
          />
        </div>
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="is_public"
            checked={is_public}
            onChange={(e) => setIsPublic(e.target.checked)}
            className="rounded"
          />
          <label htmlFor="is_public" className="text-sm font-medium text-gray-700">
            Pública
          </label>
        </div>
        <div className="flex gap-3 pt-4">
          <button
            type="submit"
            disabled={submitLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {submitLoading ? "Creando…" : "Crear"}
          </button>
          <button
            type="button"
            onClick={() => navigate("/pages")}
            className="px-4 py-2 border border-gray-300 rounded font-medium text-gray-700 hover:bg-gray-50"
          >
            Cancelar
          </button>
        </div>
      </form>
    </div>
  )
}

