import { BrowserRouter, Routes, Route, Link, useLocation, useNavigate } from "react-router-dom";
import { Layout, Menu, Typography, Button } from "antd";
import {
  DashboardOutlined,
  AppstoreOutlined,
  PrinterOutlined,
  LogoutOutlined,
} from "@ant-design/icons";

import TodayPage from "./pages/TodayPage";
import ProductsPage from './pages/ProductsPage';
import PrintersPage from './pages/PrintersPage';
import ProductDetailPage from './pages/ProductDetailPage';
import ProductionPage from "./pages/ProductionPage";
import { ToolOutlined } from "@ant-design/icons"; 
import LoginPage from "./pages/LoginPage";
import ProtectedRoute from "./components/ProtectedRoute";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { logout } from "./api/auth";
import WarehousePage from "./pages/WarehousePage";
import { ShopOutlined } from "@ant-design/icons";
import PromotionsPage from "./pages/PromotionsPage";
import { TagOutlined } from "@ant-design/icons";
import SettingsPage from "./pages/SettingsPage";
import { SettingOutlined } from "@ant-design/icons";


const { Header, Sider, Content } = Layout;
const { Title } = Typography;

function SideMenu() {
  const location = useLocation();
  return (
    <Menu
      theme="dark"
      mode="inline"
      selectedKeys={[location.pathname]}
      items={[
      { key: "/", icon: <DashboardOutlined />, label: <Link to="/">Сегодня</Link> },
      { key: "/products", icon: <AppstoreOutlined />, label: <Link to="/products">Товары</Link> },
      { key: "/production", icon: <ToolOutlined />, label: <Link to="/production">Производство</Link> },
      { key: "/warehouse", icon: <ShopOutlined />, label: <Link to="/warehouse">Склад</Link> },
      { key: "/promotions", icon: <TagOutlined />, label: <Link to="/promotions">Акции</Link> },
      { key: "/printers", icon: <PrinterOutlined />, label: <Link to="/printers">Принтеры</Link> },
      { key: "/settings", icon: <SettingOutlined />, label: <Link to="/settings">Настройки</Link> },
    ]}
    />
  );
}

function AppShell() {
  const { me, setMe } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const onLogout = async () => {
    try {
      await logout();
    } finally {
      setMe(null);
      navigate("/login");
    }
  };

  // страница логина — без layout
  if (location.pathname === "/login") {
    return <LoginPage />;
  }

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider>
        <div style={{ padding: 16, color: "white" }}>
          <Title level={4} style={{ color: "white", margin: 0 }}>
            HCF
          </Title>
        </div>
        <SideMenu />
      </Sider>
      <Layout>
        <Header style={{
          background: "#fff", padding: 16,
          display: "flex", justifyContent: "space-between", alignItems: "center",
        }}>
          <Title level={5} style={{ margin: 0 }}>HandyCraftFlow</Title>
          {me && (
            <div>
              <span style={{ marginRight: 16 }}>{me.username}</span>
              <Button icon={<LogoutOutlined />} onClick={onLogout}>Выйти</Button>
            </div>
          )}
        </Header>
        <Content style={{ margin: 16 }}>
          <ProtectedRoute>
            <Routes>
              <Route path="/" element={<TodayPage />} />
              <Route path="/products" element={<ProductsPage />} />
              <Route path="/products/:id" element={<ProductDetailPage />} />
              <Route path="/printers" element={<PrintersPage />} />
              <Route path="/production" element={<ProductionPage />} />
              <Route path="/warehouse" element={<WarehousePage />} />
              <Route path="/promotions" element={<PromotionsPage />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Routes>
          </ProtectedRoute>
        </Content>
      </Layout>
    </Layout>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppShell />
      </AuthProvider>
    </BrowserRouter>
  );
}