import { BrowserRouter, Routes, Route, Link, useLocation } from "react-router-dom";
import { Layout, Menu, Typography } from "antd";
import {
  DashboardOutlined,
  AppstoreOutlined,
  PrinterOutlined,
} from "@ant-design/icons";

import TodayPage from "./pages/TodayPage";
import ProductsPage from "./pages/ProductsPage";
import PrintersPage from "./pages/PrintersPage";

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
        { key: "/printers", icon: <PrinterOutlined />, label: <Link to="/printers">Принтеры</Link> },
      ]}
    />
  );
}

export default function App() {
  return (
    <BrowserRouter>
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
          <Header style={{ background: "#fff", padding: 16 }}>
            <Title level={5} style={{ margin: 0 }}>
              HandyCraftFlow
            </Title>
          </Header>
          <Content style={{ margin: 16 }}>
            <Routes>
              <Route path="/" element={<TodayPage />} />
              <Route path="/products" element={<ProductsPage />} />
              <Route path="/printers" element={<PrintersPage />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </BrowserRouter>
  );
}