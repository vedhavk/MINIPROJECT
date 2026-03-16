import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Sprout, Stethoscope, Shield, Upload, ArrowRight } from "lucide-react";
import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-linear-to-b from-slate-50 to-slate-100 flex items-center justify-center p-4">
      <div className="w-full max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <div className="bg-linear-to-br from-teal-500 to-teal-600 p-3 rounded-2xl shadow-lg">
              <svg
                className="w-10 h-10 text-white"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M8.5 5c-1.33 0-2.42.83-2.83 2H4c-.55 0-1 .45-1 1s.45 1 1 1h1.67c.41 1.17 1.5 2 2.83 2 1.33 0 2.42-.83 2.83-2H20c.55 0 1-.45 1-1s-.45-1-1-1h-8.67c-.41-1.17-1.5-2-2.83-2zm0 2c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm7 3c-1.33 0-2.42.83-2.83 2H4c-.55 0-1 .45-1 1s.45 1 1 1h8.67c.41 1.17 1.5 2 2.83 2 1.33 0 2.42-.83 2.83-2H20c.55 0 1-.45 1-1s-.45-1-1-1h-1.67c-.41-1.17-1.5-2-2.83-2zm0 2c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1z" />
              </svg>
            </div>
          </div>
          <h1 className="text-4xl font-bold text-teal-600 mb-2">Duck Track</h1>
          <p className="text-xl text-slate-600 font-medium">
            Smart Duck Monitoring System
          </p>
          <p className="text-sm text-slate-500 mt-2">
            Select your role to continue
          </p>
        </div>

        {/* Role Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          {/* Farmer Card */}
          <Card className="bg-white hover:shadow-xl transition-all duration-300 border-slate-200">
            <CardContent className="pt-8 pb-6 text-center">
              <div className="mx-auto mb-6 w-16 h-16 bg-green-500 rounded-2xl flex items-center justify-center shadow-lg">
                <Sprout className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-slate-800 mb-3">Farmer</h2>
              <p className="text-slate-600 mb-6 min-h-12">
                Monitor your ducks with simple visual dashboard
              </p>
              <Link href="/login/farmer">
                <Button className="w-full bg-green-500 hover:bg-green-600 text-white font-medium py-5 rounded-lg group">
                  Sign In as Farmer
                  <ArrowRight className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Veterinarian Card */}
          <Card className="bg-white hover:shadow-xl transition-all duration-300 border-slate-200">
            <CardContent className="pt-8 pb-6 text-center">
              <div className="mx-auto mb-6 w-16 h-16 bg-blue-500 rounded-2xl flex items-center justify-center shadow-lg">
                <Stethoscope className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-slate-800 mb-3">
                Veterinarian
              </h2>
              <p className="text-slate-600 mb-6 min-h-12">
                Advanced health monitoring and disease detection
              </p>
              <Link href="/login/veterinarian">
                <Button className="w-full bg-blue-500 hover:bg-blue-600 text-white font-medium py-5 rounded-lg group">
                  Sign In as Veterinarian
                  <ArrowRight className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* System Admin Card */}
          <Card className="bg-white hover:shadow-xl transition-all duration-300 border-slate-200">
            <CardContent className="pt-8 pb-6 text-center">
              <div className="mx-auto mb-6 w-16 h-16 bg-slate-700 rounded-2xl flex items-center justify-center shadow-lg">
                <Shield className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-slate-800 mb-3">
                System Admin
              </h2>
              <p className="text-slate-600 mb-6 min-h-12">
                Manage system, train models, and control settings
              </p>
              <Link href="/login/admin">
                <Button className="w-full bg-slate-700 hover:bg-slate-800 text-white font-medium py-5 rounded-lg group">
                  Sign In as System Admin
                  <ArrowRight className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>

        {/* Quick Upload Section */}
        <div className="border-4 border-dashed border-yellow-400 rounded-2xl bg-yellow-50/50 p-6 mb-6">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-4">
              <div className="bg-orange-500 p-3 rounded-xl shadow-md">
                <Upload className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-slate-800 mb-1">
                  Quick Upload for Farmers
                </h3>
                <p className="text-slate-700 mb-1">
                  Upload and analyze duck images without creating an account
                </p>
                <p className="text-xs text-slate-600">
                  No personal details required • Fast & Easy • Private
                </p>
              </div>
            </div>
            <Button className="bg-orange-500 hover:bg-orange-600 text-white font-medium px-6 py-5 rounded-lg whitespace-nowrap">
              <Upload className="w-4 h-4 mr-2" />
              Upload Without Login
            </Button>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center">
          <p className="text-slate-600">
            Don&apos;t have an account?{" "}
            <Link
              href="/signup"
              className="text-green-600 hover:text-green-700 font-semibold hover:underline"
            >
              Create a free account
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
