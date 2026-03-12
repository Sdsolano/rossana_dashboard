import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"

interface PublicPageDetail {
  id: number
  slug: string
  title: string
  body: string
}

export default function PublicPage() {
  const { slug } = useParams<{ slug: string }>()
  const [page, setPage] = useState<PublicPageDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!slug) return
    setLoading(true)
    fetch(`/api/public/pages/${slug}/`)
      .then((r) => {
        if (r.ok) return r.json()
        if (r.status === 404) throw new Error("Página no encontrada")
        throw new Error("Error al cargar página")
      })
      .then((data) => {
        setPage(data)
        setError(null)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [slug])

  if (!slug) return <p className="p-6 text-red-600">Slug no indicado.</p>
  if (loading) return <p className="p-6 text-gray-600">Cargando página…</p>
  if (error) return <p className="p-6 text-red-600">{error}</p>
  if (!page) return null

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-3xl mx-auto px-4 py-10">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">{page.title}</h1>
        <article className="prose max-w-none prose-p:mb-3 prose-headings:mt-6 prose-headings:mb-2">
          {page.body.split("\n").map((line, idx) => (
            <p key={idx} className="text-gray-800">
              {line}
            </p>
          ))}
        </article>
      </div>
    </div>
  )
}

