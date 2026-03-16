import { NextResponse } from "next/server";

export async function GET() {
  // TODO: Replace with real DB/service call and return Report[].
  // Example shape:
  // return NextResponse.json([{ id, title, date, ducks, healthy, diseased, type }]);
  return NextResponse.json(
    { message: "TODO: Implement farmer reports endpoint" },
    { status: 501 },
  );
}
