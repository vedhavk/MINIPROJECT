"use client";

import { useEffect, useState } from "react";
import { FileText, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { type Report, downloadReport, getReports } from "@/lib/mockApi";

export default function Reports() {
  const [reports, setReports] = useState<Report[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    async function loadReports() {
      try {
        const data = await getReports();
        setReports(data);
      } catch {
        setErrorMessage("Reports are not available yet.");
      } finally {
        setIsLoading(false);
      }
    }

    loadReports();
  }, []);

  const handleDownloadReport = async (reportId: number) => {
    const report = reports.find((r) => r.id === reportId);
    if (!report) return;

    const blob = await downloadReport(reportId);
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download =
      report.fileName ??
      `${report.title.replace(/\s+/g, "_")}_${report.date}.txt`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  return (
    <div className="max-w-5xl">
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <h3 className="text-lg font-bold text-slate-800 mb-4">
          Available Reports
        </h3>
        {isLoading && (
          <p className="text-sm text-slate-500">Loading reports...</p>
        )}
        {!isLoading && errorMessage && (
          <p className="text-sm text-slate-500">{errorMessage}</p>
        )}
        {!isLoading && !errorMessage && reports.length === 0 && (
          <p className="text-sm text-slate-500">No reports found.</p>
        )}
        <div className="space-y-4">
          {reports.map((report) => (
            <div
              key={report.id}
              className="flex items-center justify-between p-4 border border-slate-200 rounded-lg hover:border-green-300 hover:bg-green-50/30 transition-all"
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                  <FileText className="w-6 h-6 text-green-600" />
                </div>
                <div>
                  <h4 className="font-semibold text-slate-800">
                    {report.title}
                  </h4>
                  {(report.summary || report.date) && (
                    <p className="text-sm text-slate-600">
                      {report.summary ?? report.date}
                    </p>
                  )}
                </div>
              </div>
              <Button
                variant="outline"
                className="flex items-center gap-2"
                onClick={() => handleDownloadReport(report.id)}
              >
                <Download className="w-4 h-4" />
                Download
              </Button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
