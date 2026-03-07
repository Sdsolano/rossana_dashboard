import { BrowserRouter, Routes, Route, Link, useNavigate } from "react-router-dom"
import "./App.css"
import { AuthProvider, useAuth } from "./context/AuthContext"
import Therapists from "./pages/Therapists"
import TherapistNew from "./pages/TherapistNew"
import TherapistEdit from "./pages/TherapistEdit"
import TherapistPassword from "./pages/TherapistPassword"
import Login from "./pages/Login"
import Panel from "./pages/Panel"
import PanelAvailability from "./pages/PanelAvailability"

function Nav() {
  const { isAuthenticated, logout } = useAuth()
  const navigate = useNavigate()
  return (
    <nav className="border-b border-gray-200 bg-white px-6 py-3">
      <div className="max-w-5xl mx-auto flex flex-wrap items-center gap-4">
        <Link to="/" className="text-gray-600 hover:text-gray-900 font-medium">
          Inicio
        </Link>
        <Link to="/therapists" className="text-gray-600 hover:text-gray-900 font-medium">
          Terapeutas
        </Link>
        {isAuthenticated ? (
          <>
            <Link to="/panel" className="text-gray-600 hover:text-gray-900 font-medium">
              Panel
            </Link>
            <Link to="/panel/availability" className="text-gray-600 hover:text-gray-900 font-medium">
              Mi disponibilidad
            </Link>
            <button
              type="button"
              onClick={() => { logout(); navigate("/login"); }}
              className="text-gray-600 hover:text-gray-900 font-medium"
            >
              Cerrar sesión
            </button>
          </>
        ) : (
          <Link to="/login" className="text-gray-600 hover:text-gray-900 font-medium">
            Entrar
          </Link>
        )}
      </div>
    </nav>
  )
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Nav />
      <main>
        <Routes>
          <Route
            path="/"
            element={
              <div className="p-6 max-w-5xl mx-auto">
                <h1 className="text-2xl font-semibold text-gray-800">
                  Rossana Dashboard
                </h1>
                <p className="mt-2 text-gray-600">
                  Migración legacy → Backend + Frontend. Módulo: Terapeutas.
                </p>
              </div>
            }
          />
          <Route path="/therapists" element={<Therapists />} />
          <Route path="/therapists/new" element={<TherapistNew />} />
          <Route path="/therapists/:id/edit" element={<TherapistEdit />} />
          <Route path="/therapists/:id/password" element={<TherapistPassword />} />
          <Route path="/login" element={<Login />} />
          <Route path="/panel" element={<Panel />} />
          <Route path="/panel/availability" element={<PanelAvailability />} />
        </Routes>
      </main>
    </BrowserRouter>
    </AuthProvider>
  )
}

export default App
