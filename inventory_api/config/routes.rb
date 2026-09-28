# Maps URLs and HTTP methods to controller actions
# Produces the following:
# GET  /inventory_uploads.json → inventory_uploads#index - command list_uploads - performs #index and returns summaries as JSON
# POST /inventory_uploads.json → inventory_uploads#create - performs #create and returns HTTP 201 with batch ID and record count if valid, otherwise HTTP 422 with validation errors

Rails.application.routes.draw do
  resources :inventory_uploads, only: %i[index create]

  # Define your application routes per the DSL in https://guides.rubyonrails.org/routing.html

  # Reveal health status on /up that returns 200 if the app boots with no exceptions, otherwise 500.
  # Can be used by load balancers and uptime monitors to verify that the app is live.
  get "up" => "rails/health#show", as: :rails_health_check

  # Defines the root path route ("/")
  # root "posts#index"
end
