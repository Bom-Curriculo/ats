<x-app-layout>
    <x-slot name="header">
        <h2 class="font-semibold text-xl text-gray-800 leading-tight">
            {{ __('Users') }}
        </h2>
    </x-slot>

    <div class="py-12">
        <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
            <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg">
                <div class="p-6">

                    <table id="search-table" class="table w-full">
                        <thead>
                            <tr>
                                <th>
                                    <span class="flex items-center">
                                        User name / Social Name
                                    </span>
                                </th>
                                <th>
                                    <span class="flex items-center">
                                        Email
                                    </span>
                                </th>
                                <th>
                                    <span class="flex items-center">
                                        Phone
                                    </span>
                                </th>
                                <th>
                                    <span class="flex items-center">
                                        Created At
                                    </span>
                                </th>
                                <th>
                                    <span class="flex items-center">
                                        Action
                                    </span>
                                </th>
                            </tr>
                        </thead>
                        <tbody>

                            @forelse ($users as $user)
                            
                                <tr>
                                    <td class="text-blue-500 font-bolder text-heading whitespace-nowrap">
                                        {{ $user->name }}
                                        {{ $user->social_name ? ' / '.$user->social_name : '' }}
                                    </td>
                                    <td>{{ $user->email }}</td>
                                    <td>{{ $user->phone }}</td>
                                    <td>{{ $user->created_at }}</td>
                                    <td>
                                        Show,
                                        Edit,
                                        Delete
                                    </td>
                                </tr>

                            @empty

                                <tr>
                                    <td colspan="5" class="text-center">No users registered.</td>
                                </tr>
                                
                            @endforelse
                            
                        </tbody>
                    </table>

                </div>
            </div>
        </div>
    </div>

    @push('scripts')
        <script>

            if (document.getElementById("search-table") && typeof simpleDatatables.DataTable !== 'undefined') {
                const dataTable = new simpleDatatables.DataTable("#search-table", {
                    searchable: true,
                    sortable: true,
                    paging: true,
                    perPage: 5,
                    perPageSelect: [5, 10, 15, 20, 25],
                });
            }

        </script>
    @endpush
</x-app-layout>

