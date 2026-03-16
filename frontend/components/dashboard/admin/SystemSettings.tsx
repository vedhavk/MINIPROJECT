import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function SystemSettings() {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <h3 className="mb-4 text-xl font-bold text-slate-900">System Settings</h3>
      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-700">
            Detection Threshold
          </label>
          <Input defaultValue="0.65" />
        </div>
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-700">
            Alert Email
          </label>
          <Input defaultValue="alerts@ducktrack.local" />
        </div>
      </div>
      <div className="mt-4 space-y-2">
        <label className="flex items-center gap-2 text-sm text-slate-700">
          <input
            type="checkbox"
            defaultChecked
            className="h-4 w-4 rounded border-slate-300"
          />
          Enable auto retraining weekly
        </label>
        <label className="flex items-center gap-2 text-sm text-slate-700">
          <input
            type="checkbox"
            defaultChecked
            className="h-4 w-4 rounded border-slate-300"
          />
          Send critical alerts instantly
        </label>
      </div>
      <div className="mt-5">
        <Button className="bg-slate-900 hover:bg-slate-800">
          Save Settings
        </Button>
      </div>
    </section>
  );
}
