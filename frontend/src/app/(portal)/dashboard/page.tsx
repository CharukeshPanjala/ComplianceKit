import { currentUser } from "@clerk/nextjs/server";

export default async function DashboardPage() {
  const user = await currentUser();
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold">Welcome, {user?.firstName}!</h1>
      <p className="text-gray-500 mt-2">Your compliance dashboard</p>
    </div>
  );
}
