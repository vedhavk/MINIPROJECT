import { NextResponse } from "next/server";

export async function GET() {
  // TODO: Replace with real service call and return ActivityData[].
  // Example shape:
  // return NextResponse.json([{ time, active }]);
  return NextResponse.json(
    { message: "TODO: Implement farmer activity endpoint" },
    { status: 501 },
  );
}
