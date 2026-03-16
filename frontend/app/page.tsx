"use client";

import { useRef, useState, type ChangeEvent } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Sprout,
  Stethoscope,
  Shield,
  Upload,
  ArrowRight,
  ArrowLeft,
  Camera,
  Images,
  Video,
} from "lucide-react";
import Link from "next/link";

export default function Home() {
  const cameraInputRef = useRef<HTMLInputElement>(null);
  const galleryInputRef = useRef<HTMLInputElement>(null);
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);

  function handleTakePhotoClick() {
    cameraInputRef.current?.click();
  }

  function handleChooseFromGalleryClick() {
    galleryInputRef.current?.click();
  }

  function handleQuickUploadChange(event: ChangeEvent<HTMLInputElement>) {
    const files = Array.from(event.target.files ?? []);
    setSelectedFiles(files.map((file) => file.name));
  }

  return (
    <div className="min-h-screen bg-linear-to-b from-slate-50 to-slate-100 flex items-center justify-center p-4">
      <div className="w-full max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <div className="bg-[#00a693] p-3 rounded-2xl shadow-lg">
              <svg
                className="w-10 h-10 text-white"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M8.5 5c-1.33 0-2.42.83-2.83 2H4c-.55 0-1 .45-1 1s.45 1 1 1h1.67c.41 1.17 1.5 2 2.83 2 1.33 0 2.42-.83 2.83-2H20c.55 0 1-.45 1-1s-.45-1-1-1h-8.67c-.41-1.17-1.5-2-2.83-2zm0 2c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm7 3c-1.33 0-2.42.83-2.83 2H4c-.55 0-1 .45-1 1s.45 1 1 1h8.67c.41 1.17 1.5 2 2.83 2 1.33 0 2.42-.83 2.83-2H20c.55 0 1-.45 1-1s-.45-1-1-1h-1.67c-.41-1.17-1.5-2-2.83-2zm0 2c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1z" />
              </svg>
            </div>
          </div>
          <h1 className="text-4xl font-bold text-[#00a693] mb-2 font-serif">Duck Track</h1>
          <p className="text-xl text-slate-600 font-medium">
            Smart Duck Monitoring System
          </p>
          <p className="text-sm text-slate-500 mt-2">
            Upload duck images first or select your role to continue
          </p>
        </div>

        {/* Video Feed Section */}
        <div className="mb-10 w-full max-w-5xl mx-auto">
          <div className="flex items-center justify-between mb-4 px-2">
            <h2 className="text-2xl font-bold text-slate-800 font-serif"> Farmer&apos;s Quick Tool || Instant Analysis</h2>
            <Button 
              variant="outline" 
              className="bg-white border-slate-200 text-slate-600 shadow-xs hover:bg-slate-50 rounded-lg px-4 py-2 flex items-center gap-2"
              onClick={handleChooseFromGalleryClick}
            >
              <Upload className="h-4 w-4" />
              Upload 
            </Button>
          </div>
          
          <div className="relative w-full aspect-video rounded-[2.5rem] overflow-hidden bg-slate-900 border border-slate-200 shadow-2xl flex flex-col items-center justify-center p-8">
            {/* Background Texture/Image with heavy overlay */}
            <div 
              className="absolute inset-0 bg-[url('/duck-bg.jpg')] bg-cover bg-center " 
              aria-hidden="true"
            />
            
            <div className="relative z-10 flex flex-col items-center text-center">
              <div className="mb-6 p-5 rounded-3xl bg-white/5 backdrop-blur-sm border border-white/10">
                <Camera className="w-12 h-12 text-white" />
              </div>
              <h3 className="text-3xl font-bold text-white mb-3">photo/video</h3>
              <p className="text-lg text-red font-medium">Upload photo/video or start live detection</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 mt-6">
            <Button 
              className="h-14 rounded-2xl bg-linear-to-r from-[#00a693] to-[#334155] hover:opacity-90 text-white text-lg font-bold shadow-lg transition-all"
            >
              Start Detection
            </Button>
            <Button 
              className="h-14 rounded-2xl bg-[#fee2e2] hover:bg-[#fecaca] text-[#ef4444] text-lg font-bold shadow-sm transition-all border-none"
            >
              Stop Detection
            </Button>
          </div>
          
          {selectedFiles.length > 0 && (
            <div className="mt-4 p-4 bg-white rounded-xl border border-slate-200 shadow-xs">
              <p className="text-sm font-semibold text-slate-800">Selected: {selectedFiles.join(", ")}</p>
            </div>
          )}
        </div>

        {/* Role Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          {/* Farmer Card */}
          <Card className="bg-white hover:shadow-xl transition-all duration-300 border-slate-200">
            <CardContent className="pt-8 pb-6 text-center">
              <div className="mx-auto mb-6 w-16 h-16 bg-[#00a693] rounded-2xl flex items-center justify-center shadow-lg">
                <Sprout className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-slate-800 mb-3 font-serif">Farmer</h2>
              <p className="text-slate-600 mb-6 min-h-12">
                Monitor your ducks with simple visual dashboard
              </p>
              <Link href="/login/farmer">
                <Button className="w-full bg-[#00a693] hover:opacity-90 text-white font-medium py-5 rounded-lg group">
                  Sign In as Farmer
                  <ArrowRight className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Veterinarian Card */}
          <Card className="bg-white hover:shadow-xl transition-all duration-300 border-slate-200">
            <CardContent className="pt-8 pb-6 text-center">
              <div className="mx-auto mb-6 w-16 h-16 bg-[#334155] rounded-2xl flex items-center justify-center shadow-lg">
                <Stethoscope className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-slate-800 mb-3 font-serif">
                Veterinarian
              </h2>
              <p className="text-slate-600 mb-6 min-h-12">
                Advanced health monitoring and disease detection
              </p>
              <Link href="/login/veterinarian">
                <Button className="w-full bg-[#334155] hover:bg-slate-800 text-white font-medium py-5 rounded-lg group">
                  Sign In as Veterinarian
                  <ArrowRight className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* System Admin Card */}
          <Card className="bg-white hover:shadow-xl transition-all duration-300 border-slate-200">
            <CardContent className="pt-8 pb-6 text-center">
              <div className="mx-auto mb-6 w-16 h-16 bg-[#334155] rounded-2xl flex items-center justify-center shadow-lg">
                <Shield className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-slate-800 mb-3 font-serif">
                System Admin
              </h2>
              <p className="text-slate-600 mb-6 min-h-12">
                Manage system, train models, and control settings
              </p>
              <Link href="/login/admin">
                <Button className="w-full bg-[#334155] hover:bg-slate-800 text-white font-medium py-5 rounded-lg group">
                  Sign In as System Admin
                  <ArrowRight className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>

        {/* Footer */}
        <div className="text-center">
          <p className="text-slate-600">
            Don&apos;t have an account?{" "}
            <Link
              href="/signup"
              className="text-[#00a693] hover:opacity-80 font-semibold hover:underline"
            >
              Create a free account
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
