"use client";

import { useState } from "react";
import Link from "next/link";
import {
  LayoutDashboard,
  FileText,
  Activity,
  Settings,
  LogOut,
  Sprout,
  Download,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { generateLatestReport } from "@/lib/mockApi";
import FarmDashboard from "@/components/dashboard/farmer/FarmDashboard";
import Reports from "@/components/dashboard/farmer/Reports";
import DuckActivity from "@/components/dashboard/farmer/DuckActivity";
import SettingsPage from "@/components/dashboard/farmer/Settings";

export default function FarmerDashboardPage() {
  const [activeMenu, setActiveMenu] = useState("dashboard");

  const menuItems = [
    { id: "dashboard", label: "My Farm Dashboard", icon: LayoutDashboard },
    { id: "reports", label: "My Reports", icon: FileText },
    { id: "activity", label: "Duck Activity", icon: Activity },
    { id: "settings", label: "Settings", icon: Settings },
  ];

  return (
    <div className="flex h-screen bg-slate-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-slate-200 flex flex-col">
        {/* Logo and Header */}
        <div className="p-6 border-b border-slate-200">
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-linear-to-br from-teal-500 to-teal-600 p-2 rounded-xl">
              <svg
                className="w-6 h-6 text-white"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M8.5 5c-1.33 0-2.42.83-2.83 2H4c-.55 0-1 .45-1 1s.45 1 1 1h1.67c.41 1.17 1.5 2 2.83 2 1.33 0 2.42-.83 2.83-2H20c.55 0 1-.45 1-1s-.45-1-1-1h-8.67c-.41-1.17-1.5-2-2.83-2zm0 2c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm7 3c-1.33 0-2.42.83-2.83 2H4c-.55 0-1 .45-1 1s.45 1 1 1h8.67c.41 1.17 1.5 2 2.83 2 1.33 0 2.42-.83 2.83-2H20c.55 0 1-.45 1-1s-.45-1-1-1h-1.67c-.41-1.17-1.5-2-2.83-2zm0 2c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1z" />
              </svg>
            </div>
            <div>
              <h1 className="text-lg font-bold text-teal-600">Duck Track</h1>
              <p className="text-xs text-slate-500">Farmer Dashboard</p>
            </div>
          </div>
        </div>

        {/* Menu Items */}
        <nav className="flex-1 p-4">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3 px-3">
            Farmer Menu
          </p>
          <div className="space-y-1">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeMenu === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveMenu(item.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                    isActive
                      ? "bg-linear-to-r from-green-500 to-blue-500 text-white shadow-md"
                      : "text-slate-700 hover:bg-slate-100"
                  }`}
                >
                  <Icon
                    className={`w-5 h-5 ${isActive ? "text-white" : "text-slate-600"}`}
                  />
                  <span className="font-medium text-sm">{item.label}</span>
                </button>
              );
            })}
          </div>
        </nav>

        {/* Account Info */}
        <div className="p-4">
          <div className="bg-teal-50 rounded-xl p-4 border border-teal-100">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-green-500 rounded-lg flex items-center justify-center">
                <Sprout className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-800">
                  Farmer Account
                </p>
                <p className="text-xs text-slate-600">Simple monitoring</p>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col">
        {/* Top Bar */}
        <header className="bg-white border-b border-slate-200 px-8 py-4 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-slate-800">
              {menuItems.find((item) => item.id === activeMenu)?.label}
            </h2>
            {activeMenu === "reports" && (
              <p className="text-sm text-slate-600 mt-1">
                View and download your duck farm reports
              </p>
            )}
            {activeMenu === "activity" && (
              <p className="text-sm text-slate-600 mt-1">
                Monitor your ducks&apos; daily activities
              </p>
            )}
          </div>
          <div className="flex items-center gap-3">
            {activeMenu === "reports" && (
              <Button
                onClick={() => generateLatestReport()}
                className="bg-green-500 hover:bg-green-600 text-white flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Download Latest Report
              </Button>
            )}
            <Link href="/">
              <Button
                variant="ghost"
                className="flex items-center gap-2 text-slate-600 hover:text-slate-800"
              >
                <LogOut className="w-4 h-4" />
                Logout
              </Button>
            </Link>
          </div>
        </header>

        {/* Content Area */}
        <div className="flex-1 p-8 overflow-auto">
          {activeMenu === "dashboard" && <FarmDashboard />}
          {activeMenu === "reports" && <Reports />}
          {activeMenu === "activity" && <DuckActivity />}
          {activeMenu === "settings" && <SettingsPage />}
        </div>
      </main>
    </div>
  );
}
