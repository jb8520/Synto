import os
import datetime
import discord
from discord.ext import commands

from services.auto_vc import AutoVcRuntime
from services.counting import CountingSaveRuntime
from ui.views.auto_vc import AutoVcButtons


class Synto(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix = '?',
            intents = discord.Intents.all(),
            case_insensitive = True,
        )

        self.auto_vc_runtime = AutoVcRuntime()
        self.counting_save_runtime = CountingSaveRuntime()
        self.time = datetime.datetime.now()


    def register_persistent_views(self):
        persistent_views = [
            AutoVcButtons()
        ]

        for view in persistent_views:
            self.add_view(view)
    

    async def load_cogs(self):
        extension_message = 'cogs: '
        count = 0

        for filename in os.listdir('./cogs'):
            if not filename.endswith('.py') or filename.startswith('__'):
                continue
            
            extension_name = f'cogs.{filename[:-3]}'
            try:
                await self.load_extension(extension_name)
                extension_message += f'{filename[:-3]}, '
                count += 1
            except Exception as error:
                print(
                    f'❌ Failed to load extension {extension_name}\n'
                    f'{type(error).__name__}: {error}'
                )

        if extension_message != 'cogs: ':
            extension_message = extension_message[:-2]

        print(f'✅ Successfully loaded {count} {extension_message}')


    async def setup_hook(self):
        self.remove_command('help')
        self.register_persistent_views()
        await self.load_cogs()
        
    async def on_ready(self):
        await self.change_presence(
            activity = discord.Activity(
                name = '/settings',
                type = discord.ActivityType.watching,
            )
        )
        print(
            f'{self.user} is connected to Discord, '
            f'current latency is {round(self.latency * 1000)}ms'
        )