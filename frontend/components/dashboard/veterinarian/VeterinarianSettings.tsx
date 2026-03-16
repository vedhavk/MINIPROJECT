import { Bell, Lock, MonitorDot, UserRound } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function VeterinarianSettings() {
  return (
    <div className="grid gap-6 xl:grid-cols-2">
      <section className="rounded-2xl bg-white p-6 shadow-sm">
        <div className="mb-5 flex items-center gap-3">
          <div className="rounded-xl bg-blue-100 p-3">
            <UserRound className="h-5 w-5 text-blue-600" />
          </div>
          <h3 className="text-xl font-bold text-slate-900">Profile Settings</h3>
        </div>
        <div className="space-y-4">
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">
              Full Name
            </label>
            <Input placeholder="Dr. Jane Smith" />
          </div>
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">
              Email
            </label>
            <Input placeholder="vet@example.com" type="email" />
          </div>
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">
              License Number
            </label>
            <Input placeholder="VET-12345" />
          </div>
          <Button className="bg-blue-600 hover:bg-blue-700">
            Save Profile
          </Button>
        </div>
      </section>

      <section className="rounded-2xl bg-white p-6 shadow-sm">
        <div className="mb-5 flex items-center gap-3">
          <div className="rounded-xl bg-violet-100 p-3">
            <Lock className="h-5 w-5 text-violet-600" />
          </div>
          <h3 className="text-xl font-bold text-slate-900">Security</h3>
        </div>
        <div className="space-y-4">
          <Input type="password" placeholder="Current password" />
          <Input type="password" placeholder="New password" />
          <Input type="password" placeholder="Confirm new password" />
          <Button className="bg-violet-600 hover:bg-violet-700">
            Update Password
          </Button>
        </div>
      </section>

      <section className="rounded-2xl bg-white p-6 shadow-sm">
        <div className="mb-5 flex items-center gap-3">
          <div className="rounded-xl bg-amber-100 p-3">
            <Bell className="h-5 w-5 text-amber-600" />
          </div>
          <h3 className="text-xl font-bold text-slate-900">Notifications</h3>
        </div>
        <div className="space-y-3 text-slate-700">
          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              defaultChecked
              className="h-4 w-4 rounded border-slate-300"
            />
            Critical health alerts
          </label>
          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              defaultChecked
              className="h-4 w-4 rounded border-slate-300"
            />
            Behavioral anomalies
          </label>
          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              className="h-4 w-4 rounded border-slate-300"
            />
            Daily report digest
          </label>
        </div>
      </section>

      <section className="rounded-2xl bg-white p-6 shadow-sm">
        <div className="mb-5 flex items-center gap-3">
          <div className="rounded-xl bg-emerald-100 p-3">
            <MonitorDot className="h-5 w-5 text-emerald-600" />
          </div>
          <h3 className="text-xl font-bold text-slate-900">
            Review Preferences
          </h3>
        </div>
        <div className="space-y-4 text-slate-700">
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">
              Default review queue
            </label>
            <select className="w-full rounded-lg border border-slate-300 px-3 py-2">
              <option>Health Alerts</option>
              <option>Image Review</option>
              <option>Behavior Analysis</option>
            </select>
          </div>
          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              defaultChecked
              className="h-4 w-4 rounded border-slate-300"
            />
            Auto-highlight abnormal posture detections
          </label>
          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              defaultChecked
              className="h-4 w-4 rounded border-slate-300"
            />
            Show clinical suggestions in alerts
          </label>
        </div>
      </section>
    </div>
  );
}
