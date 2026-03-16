import { Users } from "lucide-react";

import { Button } from "@/components/ui/button";
import { users } from "@/lib/adminMockApi";

export default function UserManagement() {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-xl font-bold text-slate-900">User Management</h3>
        <Button className="bg-blue-600 hover:bg-blue-700">Invite User</Button>
      </div>
      <div className="space-y-3">
        {users.map((user) => (
          <div
            key={user.id}
            className="flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 p-4"
          >
            <div className="flex items-center gap-3">
              <Users className="h-5 w-5 text-slate-600" />
              <div>
                <p className="font-semibold text-slate-900">{user.name}</p>
                <p className="text-sm text-slate-500">{user.role}</p>
              </div>
            </div>
            <span
              className={`rounded-full px-3 py-1 text-xs font-semibold ${user.status === "Active" ? "bg-emerald-100 text-emerald-700" : "bg-amber-100 text-amber-700"}`}
            >
              {user.status}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}
