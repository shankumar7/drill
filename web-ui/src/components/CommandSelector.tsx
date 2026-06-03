import { ClipboardList } from "lucide-react";
import { drillCommands } from "@/lib/commands";
import type { CommandId, DrillCommand } from "@/types/drill";

interface CommandSelectorProps {
  selectedCommand: CommandId;
  onSelectCommand: (commandId: CommandId) => void;
}

export function CommandSelector({ selectedCommand, onSelectCommand }: CommandSelectorProps) {
  const commandGroups = [
    {
      heading: "Core Commands",
      commands: drillCommands.filter((command) => command.group === "Core Commands"),
    },
    {
      heading: "LO 1.1",
      commands: drillCommands.filter((command) => command.group === "LO 1.1"),
    },
  ];

  return (
    <section className="panel p-4">
      <div className="mb-4 flex items-center gap-2">
        <ClipboardList className="h-5 w-5 text-sky-300" />
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-200">Command Selection</h2>
      </div>

      <div className="space-y-5">
        {commandGroups.map((group) => (
          <CommandGroup key={group.heading} heading={group.heading} commands={group.commands} selectedCommand={selectedCommand} onSelectCommand={onSelectCommand} />
        ))}
      </div>
    </section>
  );
}

function CommandGroup({
  heading,
  commands,
  selectedCommand,
  onSelectCommand,
}: {
  heading: string;
  commands: DrillCommand[];
  selectedCommand: CommandId;
  onSelectCommand: (commandId: CommandId) => void;
}) {
  return (
    <div>
      <div className="mb-2 flex items-center justify-between gap-3">
        <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">{heading}</div>
        <div className="text-[11px] font-medium text-slate-600">{commands.length} commands</div>
      </div>
      <div className="grid grid-cols-2 gap-2 lg:grid-cols-1">
        {commands.map((command) => {
          const isSelected = selectedCommand === command.id;

          return (
            <button
              key={command.id}
              onClick={() => onSelectCommand(command.id)}
              className={`rounded-md border p-3 text-left transition ${
                isSelected
                  ? "border-sky-400 bg-sky-500/15 text-white shadow-[0_0_0_1px_rgba(56,189,248,0.35)]"
                  : "border-white/10 bg-white/[0.03] text-slate-300 hover:border-slate-500 hover:bg-white/[0.06]"
              }`}
              aria-pressed={isSelected}
            >
              <div className="flex items-center justify-between gap-3">
                <span className="text-sm font-semibold">{command.label}</span>
                <span className={`text-[11px] font-medium ${isSelected ? "text-sky-200" : "text-slate-500"}`}>
                  {isSelected ? "Selected" : `${command.expectedDurationSec}s`}
                </span>
              </div>
              <p className="mt-1 line-clamp-2 text-xs leading-5 text-slate-500">{command.description}</p>
            </button>
          );
        })}
      </div>
    </div>
  );
}
