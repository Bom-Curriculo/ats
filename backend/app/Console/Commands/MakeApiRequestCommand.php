<?php

namespace App\Console\Commands;

use Illuminate\Console\Attributes\Description;
use Illuminate\Console\Attributes\Signature;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\File;

#[Signature('make:api-request {name}')]
#[Description('Create a new Api Request Validation')]
class MakeApiRequestCommand extends Command
{
    /**
     * Execute the console command.
     */
    public function handle()
    {
        $name = str_replace('\\', '/', $this->argument('name'));

        $className = class_basename($name);

        $namespace = 'App\\Http\\ApiRequests';

        $directory = app_path('Http/ApiRequests');

        if (str_contains($name, '/')) {
            $subPath = dirname($name);

            $namespace .= '\\'.str_replace('/', '\\', $subPath);

            $directory .= '/'.$subPath;
        }

        File::ensureDirectoryExists($directory);

        $file = $directory.'/'.$className.'.php';

        if (File::exists($file)) {
            $this->error('Request already exists.');

            return self::FAILURE;
        }

        File::put(
            $file,
            $this->buildStub($namespace, $className)
        );

        $this->info("Request created successfully: {$file}");

        return self::SUCCESS;
    }

    protected function buildStub(string $namespace, string $class): string
    {
        return <<<PHP
<?php

namespace {$namespace};

use App\Http\ApiRequests\CustomRequest;

class {$class} extends CustomRequest
{

    public function rules(): array
    {
        return [

        ];
    }

}
PHP;
    }
}
