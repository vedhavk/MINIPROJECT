import { NextResponse } from "next/server";

export async function GET() {
  // TODO: Replace with real service call and return VetAlert[].
  return NextResponse.json(
    { message: "TODO: Implement veterinarian alerts endpoint" },
    { status: 501 },
  );
}
